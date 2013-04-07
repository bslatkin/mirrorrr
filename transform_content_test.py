#!/usr/bin/env python
# Copyright 2008 Brett Slatkin
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

__author__ = "Brett Slatkin (bslatkin@gmail.com)"

import logging
import unittest

import transform_content

################################################################################

class TransformTest(unittest.TestCase):
  
  def _RunTransformTest(self, base_url, accessed_url, original, expected):
    tag_tests = [
      '<img src="%s"/>',
      "<img src='%s'/>",
      "<img src=%s/>",
      "<img src=\"%s'/>",
      "<img src='%s\"/>",
      "<img src  \t=  '%s'/>",
      "<img src  \t=  \t '%s'/>",
      "<img src = '%s'/>",
      '<a href="%s">',
      "<a href='%s'>",
      "<a href=%s>",
      "<a href=\"%s'>",
      "<a href='%s\">",
      "<a href \t = \t'%s'>",
      "<a href \t  = '%s'>",
      "<a href =  \t'%s'>",
      "<td background=%s>",
      "<td background='%s'>",
      '<td background="%s">',
      '<form action="%s">',
      "<form action='%s'>",
      "<form action=%s>",
      "<form action=\"%s'>",
      "<form action='%s\">",
      "<form action \t = \t'%s'>",
      "<form action \t  = '%s'>",
      "<form action =  \t'%s'>",      
      "@import '%s';",
      "@import '%s'\nnext line here",
      "@import \t '%s';",
      "@import %s;",
      "@import %s",
      '@import "%s";',
      '@import "%s"\nnext line here',
      "@import url(%s)",
      "@import url('%s')",
      '@import url("%s")',
      "background: transparent url(%s) repeat-x left;",
      'background: transparent url("%s") repeat-x left;',
      "background: transparent url('%s') repeat-x left;",
      '<meta http-equiv="Refresh" content="0; URL=%s">',
    ]
    for tag in tag_tests:
      test = tag % original
      correct = tag % expected
      result = transform_content.TransformContent(base_url, accessed_url, test)
      logging.info("Test with\n"
                   "Accessed: %s\n"
                   "Input   : %s\n"
                   "Received: %s\n"
                   "Expected: %s",
                   accessed_url, test, result, correct)
      if result != correct:
        logging.info("FAIL")
      self.assertEquals(correct, result)

  def testBaseTransform(self):
    self._RunTransformTest(
      "slashdot.org",
      "http://slashdot.org",
      "//images.slashdot.org/iestyles.css?T_2_5_0_204",
      "/images.slashdot.org/iestyles.css?T_2_5_0_204")

  def testAbsolute(self):
    self._RunTransformTest(
      "slashdot.org",
      "http://slashdot.org",
      "http://slashdot.org/slashdot_files/all-minified.js",
      "/slashdot.org/slashdot_files/all-minified.js")
  
  def testRelative(self):
    self._RunTransformTest(
      "slashdot.org",
      "http://slashdot.org",
      "images/foo.html",
      "/slashdot.org/images/foo.html")
  
  def testUpDirectory(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      "http://a248.e.akamai.net/foobar/is/the/path.html",
      "../layout/mh_phone-home.png",
      "/a248.e.akamai.net/foobar/is/the/../layout/mh_phone-home.png")

  def testSameDirectoryRelative(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      "http://a248.e.akamai.net/foobar/is/the/path.html",
      "./layout/mh_phone-home.png",
      "/a248.e.akamai.net/foobar/is/the/./layout/mh_phone-home.png")

  def testSameDirectory(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      "http://a248.e.akamai.net/foobar/is/the/path.html",
      "mh_phone-home.png",
      "/a248.e.akamai.net/foobar/is/the/mh_phone-home.png")

  def testSameDirectoryNoParent(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      "http://a248.e.akamai.net/path.html",
      "mh_phone-home.png",
      "/a248.e.akamai.net/mh_phone-home.png")

  def testSameDirectoryWithParent(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      ("http://a248.e.akamai.net/7/248/2041/1447/store.apple.com"
       "/rs1/css/aos-screen.css"),
      "aos-layout.css",
      ("/a248.e.akamai.net/7/248/2041/1447/store.apple.com"
       "/rs1/css/aos-layout.css"))

  def testRootDirectory(self):
    self._RunTransformTest(
      "a248.e.akamai.net",
      "http://a248.e.akamai.net/foobar/is/the/path.html",
      "/",
      "/a248.e.akamai.net/")
  
  def testSecureContent(self):
    self._RunTransformTest(
      "slashdot.org",
      "https://slashdot.org",
      "https://images.slashdot.org/iestyles.css?T_2_5_0_204",
      "/images.slashdot.org/iestyles.css?T_2_5_0_204")

  def testPartiallySecureContent(self):
    self._RunTransformTest(
      "slashdot.org",
      "http://slashdot.org",
      "https://images.slashdot.org/iestyles.css?T_2_5_0_204",
      "/images.slashdot.org/iestyles.css?T_2_5_0_204")

################################################################################

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.DEBUG)
  unittest.main()
