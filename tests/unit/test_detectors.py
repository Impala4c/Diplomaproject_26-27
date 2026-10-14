import base64
import hashlib
import unittest

from tests import support
from secret_history.detectors import github, google, pem, slack
from secret_history.reporting.report import candidate_record


def fake_token(kind):
    body = hashlib.sha256(("never-issued-" + kind).encode()).hexdigest()
    return {"github": "ghp_" + body[:36], "google": "AIza" + body[:35],
            "slack": "xoxb-" + "123456789012-" * 2 + body[:32]}[kind]


def fake_pem(label="PRIVATE KEY"):
    body = base64.b64encode(b"\x30\x03\x02\x01\x01").decode()
    return f"-----BEGIN {label}-----\n{body}\n-----END {label}-----"


class GitHubTests(unittest.TestCase):
    def test_classic_token_families(self):
        for prefix in ("ghp_", "gho_", "ghu_", "ghs_", "ghr_"):
            candidates, issues = github.extract('token="' + prefix + fake_token("github")[4:] + '"')
            self.assertFalse(issues)
            self.assertEqual(len(candidates), 1)
            self.assertEqual(github.classify(candidates[0]).status, "SUSPECTED_SECRET")

    def test_fine_grained_and_stateless_installation_tokens(self):
        for value in ("github_pat_" + "a" * 22 + "_" + "b" * 59,
                      "ghs_12345_" + "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjB9.synthetic_signature"):
            candidates, _ = github.extract(value)
            self.assertEqual(github.classify(candidates[0]).status, "SUSPECTED_SECRET")

    def test_placeholders_public_example_and_references(self):
        for value in (*github.PUBLIC_EXAMPLES, "your_github_token", "${GITHUB_TOKEN}", ""):
            candidates, _ = github.extract("GITHUB_TOKEN=" + value)
            self.assertEqual(github.classify(candidates[0]).status, "NON_SECRET")

    def test_unknown_shapes_are_retained_and_example_context_is_not_allowlisted(self):
        for text in ("GITHUB_TOKEN=short", "# public example: " + fake_token("github")):
            candidates, _ = github.extract(text)
            self.assertNotEqual(github.classify(candidates[0]).status, "NON_SECRET")

    def test_two_tokens_on_same_line_have_distinct_stable_fingerprints(self):
        text = fake_token("github") + " " + fake_token("github")
        candidates, _ = github.extract(text)
        rows = [candidate_record(c, github.classify(c), "file.txt", "a" * 40) for c in candidates]
        self.assertEqual(len({r["fingerprint"] for r in rows}), 2)
        self.assertEqual(rows, [candidate_record(c, github.classify(c), "file.txt", "a" * 40) for c in github.extract(text)[0]])

    def test_malformed_named_assignment_is_a_coverage_warning(self):
        candidates, issues = github.extract('GITHUB_TOKEN="unclosed')
        self.assertFalse(candidates)
        self.assertEqual(len(issues), 1)

    def test_actions_reference_is_not_a_literal_but_expressions_are_not_suppressed(self):
        for value in ("${{ secrets.GITHUB_TOKEN }}", "${{secrets.TOKEN}}", "${{ github.token }}"):
            candidates, issues = github.extract("GITHUB_TOKEN: " + value)
            self.assertFalse(issues)
            self.assertEqual(github.classify(candidates[0]).status, "NON_SECRET")
        value = "${{ secrets.TOKEN || '" + fake_token("github") + "' }}"
        candidates, _ = github.extract("GITHUB_TOKEN: " + value)
        self.assertTrue(any(github.classify(c).status == "SUSPECTED_SECRET" for c in candidates))


class PemTests(unittest.TestCase):
    def test_exact_rfc7468_public_example_only(self):
        body = ("MIGEAgEAMBAGByqGSM49AgEGBSuBBAAKBG0wawIBAQQgVcB/UNPxalR9zDYAjQIf"
                "jojUDiQuGnSJrFEEzZPT/92hRANCAASc7UJtgnF/abqWM60T3XNJEzBv5ez9TdwK"
                "H0M6xpM2q+53wmsN/eYLdgtjgBd3DBmHtPilCkiFICXyaA8z9LkJ")
        value = "-----BEGIN PRIVATE KEY-----\n" + body + "\n-----END PRIVATE KEY-----"
        self.assertEqual(pem.classify(pem.extract(value)[0][0]).status, "NON_SECRET")
        modified = value.replace(body, body[:-1] + "A")
        self.assertNotEqual(pem.classify(pem.extract(modified)[0][0]).status, "NON_SECRET")

    def test_private_key_labels_and_encrypted_material(self):
        for label in ("PRIVATE KEY", "RSA PRIVATE KEY", "EC PRIVATE KEY", "DSA PRIVATE KEY", "ENCRYPTED PRIVATE KEY"):
            candidates, _ = pem.extract(fake_pem(label))
            self.assertEqual(pem.classify(candidates[0]).status, "SUSPECTED_SECRET")
            self.assertEqual(candidates[0].bindings[0].end_line, 3)

    def test_openssh_private_key_envelope(self):
        body = base64.b64encode(b"openssh-key-v1\0synthetic").decode()
        text = "-----BEGIN OPENSSH PRIVATE KEY-----\n" + body + "\n-----END OPENSSH PRIVATE KEY-----"
        self.assertEqual(pem.classify(pem.extract(text)[0][0]).status, "SUSPECTED_SECRET")

    def test_public_key_and_certificate_are_excluded(self):
        self.assertEqual(pem.extract(fake_pem("PUBLIC KEY"))[0], [])
        self.assertEqual(pem.extract(fake_pem("CERTIFICATE"))[0], [])

    def test_placeholder_and_unterminated_blocks(self):
        text = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
        self.assertEqual(pem.classify(pem.extract(text)[0][0]).status, "NON_SECRET")
        explicit = text.replace("...", "<SYNTHETIC_BODY_NOT_A_VALID_PRIVATE_KEY>")
        self.assertEqual(pem.classify(pem.extract(explicit)[0][0]).status, "NON_SECRET")
        self.assertEqual(pem.classify(pem.extract(text.split("-----END")[0])[0][0]).status, "UNCERTAIN")

    def test_public_example_context_does_not_suppress_a_complete_key(self):
        candidate = pem.extract("# example from documentation\n" + fake_pem())[0][0]
        self.assertEqual(pem.classify(candidate).status, "SUSPECTED_SECRET")
        self.assertNotIn(candidate.bindings[0].value, repr(candidate))

    def test_mismatched_end_and_multiple_blocks(self):
        text = fake_pem().replace("END PRIVATE", "END RSA PRIVATE") + "\n" + fake_pem()
        candidates, _ = pem.extract(text)
        self.assertEqual([pem.classify(c).status for c in candidates], ["UNCERTAIN", "SUSPECTED_SECRET"])


class SlackTests(unittest.TestCase):
    def test_bot_user_and_app_tokens(self):
        values = [fake_token("slack"), "xoxp-" + "123456789012-" * 3 + "a" * 32,
                  "xapp-" + "1-A123456789-1234567890123-" + "b" * 64]
        for value in values:
            self.assertEqual(slack.classify(slack.extract(value)[0][0]).status, "SUSPECTED_SECRET")

    def test_exact_documentation_example_and_placeholders(self):
        for value in (*slack.PUBLIC_EXAMPLES, "your_slack_token", "$SLACK_TOKEN", ""):
            self.assertEqual(slack.classify(slack.extract("SLACK_TOKEN=" + value)[0][0]).status, "NON_SECRET")

    def test_modified_example_and_unknown_family_shape_remain_alerts(self):
        for value in (next(iter(slack.PUBLIC_EXAMPLES)) + "A", "xoxr-" + "abc" * 12):
            self.assertEqual(slack.classify(slack.extract(value)[0][0]).status, "UNCERTAIN")


class GoogleTests(unittest.TestCase):
    def test_key_needs_context_and_restrictions_review(self):
        candidate = google.extract(fake_token("google"))[0][0]
        self.assertEqual(google.classify(candidate).status, "UNCERTAIN")
        self.assertIn("restriction", google.classify(candidate).reason)

    def test_public_placeholder_empty_and_reference(self):
        for value in (*google.PUBLIC_EXAMPLES, "${GOOGLE_API_KEY}", ""):
            self.assertEqual(google.classify(google.extract("GOOGLE_API_KEY=" + value)[0][0]).status, "NON_SECRET")

    def test_wrong_length_and_embedded_boundaries(self):
        value = fake_token("google") + "extra"
        self.assertEqual(google.classify(google.extract(value)[0][0]).reason, "unexpected_google_api_key_format")
        self.assertEqual(google.extract("prefix" + fake_token("google"))[0], [])
