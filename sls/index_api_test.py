#!/home/tops/bin/python
# -*- encoding:utf-8 -*-
import time
import unittest

from api_test_base import APITest


def log(func):
    def wrapper(self, *args, **kw):
        self._logger.info("Prepare to test %s, project=%s, _logstore=%s" %
                          (func.__name__, self._project, self._logstore))
        func(self, *args, **kw)
        self._logger.info("Test of %s is over, project=%s, _logstore=%s" %
                          (func.__name__, self._project, self._logstore))

    return wrapper


class IndexAPITest(APITest):
    """API List:
    - CreateIndex,GetIndexConfig, Update_index, DeleteIndex
    """
    def setUp(self):
        self.base_setup()
        self._index_key = "test"
        self._index_config_json = {
            'keys': {
                self._index_key: {
                    'caseSensitive':
                    True,
                    'token': [
                        '\n', '\t', ',', ' ', ';', '"', "'", '(', ')', '{',
                        '}', '[', ']', '<', '>', '?', '/', '#', ':'
                    ],
                    'type':
                    'text',
                    'doc_value':
                    False
                }
            },
            'line': {
                'caseSensitive':
                False,
                'token': [
                    '\n', '\t', ',', ' ', ';', '"', "'", '(', ')', '{', '}',
                    '[', ']', '<', '>', '?', '/', '#', ':'
                ],
                'chn':
                False
            }
        }

    def test(self):
        self._delete_index()
        self._create_index()
        self._get_index_config()
        self._update_index()

    @log
    def _delete_index(self):
        self._client.delete_index(self._project, self._logstore)
        time.sleep(3)
        try:
            self._client.get_index_config(self._project, self._logstore)
            self.assertTrue(False, msg="delete index error")
        except:
            pass

    @log
    def _create_index(self):
        self._index_config.from_json(self._index_config_json)
        self._client.create_index(self._project, self._logstore,
                                  self._index_config)
        time.sleep(3)

    @log
    def _get_index_config(self):
        index_config_json_created = self._client.get_index_config(
            self._project, self._logstore).get_index_config().to_json()
        self.assertTrue(
            self._index_key in index_config_json_created['keys'].keys())

    @log
    def _update_index(self):
        self._index_config_json["keys"][
            self._index_key]["caseSensitive"] = False
        self._index_config.from_json(self._index_config_json)
        self._client.update_index(self._project, self._logstore,
                                  self._index_config)
        time.sleep(3)
        index_config_json_updated = self._client.get_index_config(
            self._project, self._logstore).get_index_config().to_json()
        self.assertEqual(
            False, index_config_json_updated["keys"][self._index_key]
            ["caseSensitive"])

        self._client.delete_index(self._project, self._logstore)


if __name__ == '__main__':
    unittest.main()
