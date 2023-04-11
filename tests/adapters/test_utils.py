import globre
from parameterized import parameterized
from unittest import TestCase

from monolith_filemanager.adapters.utils import monolith_globre_match

class TestUtils(TestCase):

    @parameterized.expand([
        ["*",             "/path/to/foo"                 ],
        ["**",            "/path/to/foo"                 ],
        ["/path/*",       "/path/to/foo"                 ],
        ["/path/**",      "/path/to/foo"                 ],
        ["/path/to/*",    "/path/to/foo"                 ],
        ["/path?to",      "/path/to"                     ],
        ["/path[!abc]to", "path/to"                      ],
        ["a/b/*/f.txt",   "a/b/c/f.txt"                  ],
        ["a/b/*/f.txt",   "a/b/q/f.txt"                  ],
        ["a/b/*/f.txt",   "a/b/c/d/f.txt"                ],
        ["a/b/*/f.txt",   "a/b/c/d/e/f.txt"              ],
        ["/foo/bar/*",    "/foo/bar/baz"                 ],
        ["/foo/bar/*",    "/spam/eggs/baz"               ],
        ["/foo/bar/*",    "/foo/bar/bar"                 ],
        ["/*/bar/b*",     "/foo/bar/baz"                 ],
        ["/*/bar/b*",     "/foo/bar/bar"                 ],
        ["/*/[be]*/b*",   "/foo/bar/baz"                 ],
        ["/*/[be]*/b*",   "/foo/bar/bar"                 ],
        ["/foo*/bar",     "/foolicious/spamfantastic/bar"],
        ["/foo*/bar",     "/foolicious/bar"              ]
    ])
    def test_monolith_globre_match(self, shell_pattern: str, string: str):
        # Test that our home solution is equivalent to globre
        self.assertEqual(bool(monolith_globre_match(shell_pattern, string)),
                         bool(globre.match(shell_pattern, string)))
