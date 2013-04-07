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

import os
import re
import urlparse

################################################################################

# URLs that have absolute addresses
ABSOLUTE_URL_REGEX = r"(http(s?):)?//(?P<url>[^\"'> \t\)]+)"

# URLs that are relative to the base of the current hostname.
BASE_RELATIVE_URL_REGEX = r"/(?!(/)|(http(s?)://)|(url\())(?P<url>[^\"'> \t\)]*)"

# URLs that have '../' or './' to start off their paths.
TRAVERSAL_URL_REGEX = r"(?P<relative>\.(\.)?)/(?!(/)|(http(s?)://)|(url\())(?P<url>[^\"'> \t\)]*)"

# URLs that are in the same directory as the requested URL.
SAME_DIR_URL_REGEX = r"(?!(/)|(http(s?)://)|(url\())(?P<url>[^\"'> \t\)]+)"

# URL matches the root directory.
ROOT_DIR_URL_REGEX = r"(?!//(?!>))/(?P<url>)(?=[ \t\n]*[\"'\)>/])"

# Start of a tag using 'src' or 'href'
TAG_START = r"(?i)\b(?P<tag>src|href|action|url|background)(?P<equals>[\t ]*=[\t ]*)(?P<quote>[\"']?)"

# Start of a CSS import
CSS_IMPORT_START = r"(?i)@import(?P<spacing>[\t ]+)(?P<quote>[\"']?)"

# CSS url() call
CSS_URL_START = r"(?i)\burl\((?P<quote>[\"']?)"


REPLACEMENT_REGEXES = [
  (TAG_START + SAME_DIR_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(accessed_dir)s\g<url>"),

  (TAG_START + TRAVERSAL_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>%(accessed_dir)s/\g<relative>/\g<url>"),

  (TAG_START + BASE_RELATIVE_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>/%(base)s/\g<url>"),

  (TAG_START + ROOT_DIR_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>/%(base)s/"),

  # Need this because HTML tags could end with '/>', which confuses the
  # tag-matching regex above, since that's the end-of-match signal.
  (TAG_START + ABSOLUTE_URL_REGEX,
     "\g<tag>\g<equals>\g<quote>/\g<url>"),

  (CSS_IMPORT_START + SAME_DIR_URL_REGEX,
     "@import\g<spacing>\g<quote>%(accessed_dir)s\g<url>"),

  (CSS_IMPORT_START + TRAVERSAL_URL_REGEX,
     "@import\g<spacing>\g<quote>%(accessed_dir)s/\g<relative>/\g<url>"),

  (CSS_IMPORT_START + BASE_RELATIVE_URL_REGEX,
     "@import\g<spacing>\g<quote>/%(base)s/\g<url>"),

  (CSS_IMPORT_START + ABSOLUTE_URL_REGEX,
     "@import\g<spacing>\g<quote>/\g<url>"),

  (CSS_URL_START + SAME_DIR_URL_REGEX,
     "url(\g<quote>%(accessed_dir)s\g<url>"),
  
  (CSS_URL_START + TRAVERSAL_URL_REGEX,
      "url(\g<quote>%(accessed_dir)s/\g<relative>/\g<url>"),

  (CSS_URL_START + BASE_RELATIVE_URL_REGEX,
      "url(\g<quote>/%(base)s/\g<url>"),

  (CSS_URL_START + ABSOLUTE_URL_REGEX,
      "url(\g<quote>/\g<url>"),
]

################################################################################

def TransformContent(base_url, accessed_url, content):
  url_obj = urlparse.urlparse(accessed_url)
  accessed_dir = os.path.dirname(url_obj.path)
  if not accessed_dir.endswith("/"):
    accessed_dir += "/"

  for pattern, replacement in REPLACEMENT_REGEXES:
    fixed_replacement = replacement % {
      "base": base_url,
      "accessed_dir": accessed_dir,
    }
    content = re.sub(pattern, fixed_replacement, content)
  return content
