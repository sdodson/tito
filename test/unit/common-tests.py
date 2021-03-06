#
# Copyright (c) 2008-2009 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

""" Pure unit tests for tito's common module. """

from tito.common import *
from tito import common

import unittest

from mock import Mock


class CommonTests(unittest.TestCase):

    def test_normalize_class_name(self):
        """ Test old spacewalk.releng namespace is converted to tito. """
        self.assertEquals("tito.builder.Builder",
                normalize_class_name("tito.builder.Builder"))
        self.assertEquals("tito.builder.Builder",
                normalize_class_name("spacewalk.releng.builder.Builder"))
        self.assertEquals("tito.tagger.VersionTagger",
                normalize_class_name("spacewalk.releng.tagger.VersionTagger"))

    def test_replace_version_leading_whitespace(self):
        line = "    version='1.0'\n"
        expected = "    version='2.5.3'\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_no_whitespace(self):
        line = "version='1.0'\n"
        expected = "version='2.5.3'\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_some_whitespace(self):
        line = "version = '1.0'\n"
        expected = "version = '2.5.3'\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_double_quote(self):
        line = 'version="1.0"\n'
        expected = 'version="2.5.3"\n'
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_trailing_chars(self):
        line = "version = '1.0', blah blah blah\n"
        expected = "version = '2.5.3', blah blah blah\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_crazy_old_version(self):
        line = "version='1.0asjhd82371kjsdha98475h87asd7---asdai.**&'\n"
        expected = "version='2.5.3'\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_crazy_new_version(self):
        line = "version='1.0'\n"
        expected = "version='91asj.;]][[a]sd[]'\n"
        self.assertEquals(expected, replace_version(line,
            "91asj.;]][[a]sd[]"))

    def test_replace_version_uppercase(self):
        line = "VERSION='1.0'\n"
        expected = "VERSION='2.5.3'\n"
        self.assertEquals(expected, replace_version(line, "2.5.3"))

    def test_replace_version_no_match(self):
        line = "this isn't a version fool.\n"
        self.assertEquals(line, replace_version(line, "2.5.3"))

    def test_extract_sha1(self):
        ls_remote_output = "Could not chdir to home directory\n" + \
                           "fe87e2b75ed1850718d99c797cc171b88bfad5ca ref/origin/sometag"
        self.assertEquals("fe87e2b75ed1850718d99c797cc171b88bfad5ca",
                          extract_sha1(ls_remote_output))

    def test_compare_version(self):
        self.assertEquals(0, compare_version("1", "1"))
        self.assertTrue(compare_version("2.1", "2.2") < 0)
        self.assertTrue(compare_version("3.0.4.10", "3.0.4.2") > 0)
        self.assertTrue(compare_version("4.08", "4.08.01") < 0)
        self.assertTrue(compare_version("3.2.1.9.8144", "3.2") > 0)
        self.assertTrue(compare_version("3.2", "3.2.1.9.8144") < 0)
        self.assertTrue(compare_version("1.2", "2.1") < 0)
        self.assertTrue(compare_version("2.1", "1.2") > 0)
        self.assertTrue(compare_version("1.0", "1.0.1") < 0)
        self.assertTrue(compare_version("1.0.1", "1.0") > 0)
        self.assertEquals(0, compare_version("5.6.7", "5.6.7"))
        self.assertEquals(0, compare_version("1.01.1", "1.1.1"))
        self.assertEquals(0, compare_version("1.1.1", "1.01.1"))
        self.assertEquals(0, compare_version("1", "1.0"))
        self.assertEquals(0, compare_version("1.0", "1"))
        self.assertEquals(0, compare_version("1.0.2.0", "1.0.2"))

    def test_run_command_print(self):
        self.assertEquals('', run_command_print("sleep 0.1"))

    def test_rpmbuild_claims_to_be_successful(self):
        succeeded_result = "success"
        output = "Wrote: %s" % succeeded_result

        success_line = find_wrote_in_rpmbuild_output(output)

        self.assertEquals(succeeded_result, success_line[0])

    def test_rpmbuild_which_ended_with_error_is_described_with_the_analyzed_line(self):
        output = "some error output from rpmbuild\n" \
            "next error line"

        common.error_out = Mock()

        find_wrote_in_rpmbuild_output(output)

        common.error_out.assert_called_once_with("Unable to locate 'Wrote: ' lines in rpmbuild output: '%s'" % output)


class VersionMathTest(unittest.TestCase):
    def test_increase_version_minor(self):
        line = "1.0.0"
        expected = "1.0.1"
        self.assertEquals(expected, increase_version(line))

    def test_increase_version_major(self):
        line = "1.0"
        expected = "1.1"
        self.assertEquals(expected, increase_version(line))

    def test_increase_release(self):
        line = "1"
        expected = "2"
        self.assertEquals(expected, increase_version(line))

    def test_underscore_release(self):
        line = "1_PG5"
        expected = "2_PG5"
        self.assertEquals(expected, increase_version(line))

    def test_increase_versionless(self):
        line = "%{app_version}"
        expected = "%{app_version}"
        self.assertEquals(expected, increase_version(line))

    def test_increase_release_with_rpm_cruft(self):
        line = "1%{?dist}"
        expected = "2%{?dist}"
        self.assertEquals(expected, increase_version(line))

    def test_increase_release_with_zstream(self):
        line = "1%{?dist}.1"
        expected = "1%{?dist}.2"
        self.assertEquals(expected, increase_version(line))

    def test_unknown_version(self):
        line = "somethingstrange"
        expected = "somethingstrange"
        self.assertEquals(expected, increase_version(line))

    def test_empty_string(self):
        line = ""
        expected = ""
        self.assertEquals(expected, increase_version(line))

    def test_increase_zstream(self):
        line = "1%{?dist}"
        expected = "1%{?dist}.1"
        self.assertEquals(expected, increase_zstream(line))

    def test_increase_zstream_already_appended(self):
        line = "1%{?dist}.1"
        expected = "1%{?dist}.2"
        self.assertEquals(expected, increase_zstream(line))

    def test_reset_release_with_rpm_cruft(self):
        line = "2%{?dist}"
        expected = "1%{?dist}"
        self.assertEquals(expected, reset_release(line))

    def test_reset_release_with_more_rpm_cruft(self):
        line = "2.beta"
        expected = "1.beta"
        self.assertEquals(expected, reset_release(line))

    def test_reset_release(self):
        line = "2"
        expected = "1"
        self.assertEquals(expected, reset_release(line))


class ExtractBugzillasTest(unittest.TestCase):

    def test_single_line(self):
        commit_log = "- 123456: Did something interesting."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(1, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])

    def test_single_with_dash(self):
        commit_log = "- 123456 - Did something interesting."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(1, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])

    def test_single_with_no_spaces(self):
        commit_log = "- 123456-Did something interesting."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(1, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])

    def test_diff_format(self):
        commit_log = "+- 123456: Did something interesting."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(1, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])

    def test_single_line_no_bz(self):
        commit_log = "- Did something interesting."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(0, len(results))

    def test_multi_line(self):
        commit_log = "- 123456: Did something interesting.\n- Another commit.\n" \
            "- 456789: A third commit."
        extractor = BugzillaExtractor(commit_log)
        results = extractor.extract()
        self.assertEquals(2, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])
        self.assertEquals("Resolves: #456789 - A third commit.",
                results[1])

    def test_single_required_flag_found(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-1.0+', 'pm_ack+'])
        bug1 = ('123456', 'Did something interesting.')
        extractor._extract_bzs = Mock(return_value=[
            bug1])
        extractor._check_for_bugzilla_creds = Mock()

        extractor._load_bug = Mock(
            return_value=MockBug(bug1[0], ['myos-1.0+', 'pm_ack+']))

        results = extractor.extract()

        self.assertEquals(1, len(extractor.bzs))
        self.assertEquals(bug1[0], extractor.bzs[0][0])
        self.assertEquals(bug1[1], extractor.bzs[0][1])

        self.assertEquals(1, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])

    def test_required_flags_found(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-1.0+', 'pm_ack+'])
        bug1 = ('123456', 'Did something interesting.')
        bug2 = ('444555', 'Something else.')
        bug3 = ('987654', 'Such amaze!')
        extractor._extract_bzs = Mock(return_value=[
            bug1, bug2, bug3])
        extractor._check_for_bugzilla_creds = Mock()

        bug_mocks = [
            MockBug(bug1[0], ['myos-1.0+', 'pm_ack+']),
            MockBug(bug2[0], ['myos-2.0?', 'pm_ack?']),
            MockBug(bug3[0], ['myos-1.0+', 'pm_ack+'])]

        def next_bug(*args):
            return bug_mocks.pop(0)

        extractor._load_bug = Mock(side_effect=next_bug)

        results = extractor.extract()

        self.assertEquals(2, len(extractor.bzs))
        self.assertEquals(bug1[0], extractor.bzs[0][0])
        self.assertEquals(bug1[1], extractor.bzs[0][1])
        self.assertEquals(bug3[0], extractor.bzs[1][0])
        self.assertEquals(bug3[1], extractor.bzs[1][1])

        self.assertEquals(2, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])
        self.assertEquals("Resolves: #987654 - Such amaze!",
                results[1])

    def test_required_flags_missing(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-2.0+'])
        bug1 = ('123456', 'Did something interesting.')
        bug2 = ('444555', 'Something else.')
        bug3 = ('987654', 'Such amaze!')
        extractor._extract_bzs = Mock(return_value=[
            bug1, bug2, bug3])
        extractor._check_for_bugzilla_creds = Mock()

        bug_mocks = [
            MockBug(bug1[0], ['myos-1.0+', 'pm_ack+']),
            MockBug(bug2[0], ['myos-2.0?', 'pm_ack?']),
            MockBug(bug3[0], ['myos-1.0+', 'pm_ack+'])]

        def next_bug(*args):
            return bug_mocks.pop(0)

        extractor._load_bug = Mock(side_effect=next_bug)

        results = extractor.extract()

        self.assertEquals(0, len(extractor.bzs))
        self.assertEquals(0, len(results))

    def test_required_flags_missing_with_placeholder(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-2.0+'], placeholder_bz="54321")
        bug1 = ('123456', 'Did something interesting.')
        extractor._extract_bzs = Mock(return_value=[
            bug1])
        extractor._check_for_bugzilla_creds = Mock()

        extractor._load_bug = Mock(
            return_value=MockBug(bug1[0], ['myos-1.0+', 'pm_ack+']))

        results = extractor.extract()

        self.assertEquals(0, len(extractor.bzs))

        self.assertEquals(1, len(results))
        self.assertEquals("Related: #54321", results[0])

    def test_same_id_multiple_times(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-1.0+', 'pm_ack+'])
        bug1 = ('123456', 'Did something interesting.')
        bug3 = ('123456', 'Oops, lets try again.')
        extractor._extract_bzs = Mock(return_value=[
            bug1, bug3])
        extractor._check_for_bugzilla_creds = Mock()

        extractor._load_bug = Mock(
            return_value=MockBug(bug1[0], ['myos-1.0+', 'pm_ack+']))

        results = extractor.extract()

        self.assertEquals(2, len(extractor.bzs))
        self.assertEquals(bug1[0], extractor.bzs[0][0])
        self.assertEquals(bug1[1], extractor.bzs[0][1])
        self.assertEquals(bug3[0], extractor.bzs[1][0])
        self.assertEquals(bug3[1], extractor.bzs[1][1])

        self.assertEquals(2, len(results))
        self.assertEquals("Resolves: #123456 - Did something interesting.",
                results[0])
        self.assertEquals("Resolves: #123456 - Oops, lets try again.",
                results[1])

    def test_bug_doesnt_exist(self):

        extractor = BugzillaExtractor("", required_flags=[
            'myos-1.0+', 'pm_ack+'])
        bug1 = ('123456', 'Did something interesting.')
        extractor._extract_bzs = Mock(return_value=[
            bug1])
        extractor._check_for_bugzilla_creds = Mock()

        from tito.compat import xmlrpclib
        extractor._load_bug = Mock(side_effect=xmlrpclib.Fault("", ""))

        results = extractor.extract()

        self.assertEquals(0, len(extractor.bzs))
        self.assertEquals(0, len(results))


class MockBug(object):
    def __init__(self, bug_id, flags):
        self.flags = {}
        for flag in flags:
            self.flags[flag[0:-1]] = flag[-1]

    def get_flag_status(self, flag):
        if flag in self.flags:
            return self.flags[flag]
        else:
            return None
