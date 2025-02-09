# Copyright (C) 2017 Beijing Didi Infinity Technology and Development Co.,Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
''' text sequence to sequence task unittest '''

import os
from pathlib import Path
import numpy as np
import tensorflow as tf
from absl import logging
from delta import utils
from delta.data.task.text_seq2seq_task import TextS2STask
from delta.utils.register import import_all_modules_for_register


class TextS2STaskTest(tf.test.TestCase):
  ''' sequence to sequence task test'''

  def setUp(self):
    ''' set up'''
    import_all_modules_for_register()
    main_root = os.environ['MAIN_ROOT']
    main_root = Path(main_root)
    self.config_file = main_root.joinpath('egs/mock_text_seq2seq_data/nlp1/config/transformer-s2s.yml')

  def tearDown(self):
    ''' tear down '''

  def test_english(self):
    """ test seq to seq task of chiniese data, split sentences by space"""

    config = utils.load_config(self.config_file)
    max_len = config["model"]["net"]["structure"]["max_enc_len"]
    data_config = config["data"]
    task_config = data_config["task"]
    task_config["language"] = "english"
    task_config["split_by_space"] = False
    task_config["use_word"] = True

    # generate_mock_files(config)
    task = TextS2STask(config, utils.TRAIN)

    # test offline data
    data = task.dataset()
    self.assertTrue("input_x_dict" in data and
                    "input_enc_x" in data["input_x_dict"] and
                    "input_dec_x" in data["input_x_dict"])
    self.assertTrue("input_y_dict" in data and
                    "input_y" in data["input_y_dict"])
    with self.session() as sess:
      sess.run(data["iterator"].initializer, feed_dict=data["init_feed_dict"])
      res = sess.run([data["input_x_dict"]["input_enc_x"],
                      data["input_x_dict"]["input_dec_x"],
                      data["input_y_dict"]["input_y"],
                      data["input_x_len"]])

      logging.debug(res[0][0])
      logging.debug(res[1][0])
      logging.debug(res[2][0])
      logging.debug(res[3])

      self.assertEqual(np.shape(res[0])[0], 16)
      self.assertEqual(np.shape(res[1])[0], 16)
      self.assertEqual(np.shape(res[2])[0], 16)
      self.assertEqual(np.shape(res[3])[0], 16)

    # test online data
    export_inputs = task.export_inputs()
    self.assertTrue("export_inputs" in export_inputs and
                    "input_sentence" in export_inputs["export_inputs"])
    input_sentence = export_inputs["export_inputs"]["input_sentence"]
    input_x = export_inputs["model_inputs"]["input_enc_x"]

    with self.session() as sess:
      sess.run(data["iterator"].initializer, feed_dict=data["init_feed_dict"])
      res = sess.run(input_x, feed_dict={input_sentence: [" vice president walter "
                                                          "mondale was released"]})
      logging.debug(res[0][:5])
      logging.debug(np.shape(res[0]))
      self.assertEqual(np.shape(res[0]), (max_len,))


if __name__ == "__main__":
  logging.set_verbosity(logging.DEBUG)
  tf.test.main()
