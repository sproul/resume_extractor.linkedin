import unittest

from resume_extractor.linkedin import classify_linkedin_page


class ClassifyLinkedinPageTest(unittest.TestCase):
    def test_profile_url_is_authenticated_profile(self) -> None:
        self.assertEqual(
            "authenticated_profile",
            classify_linkedin_page(
                "https://www.linkedin.com/in/nelson-sproul/"
            ),
        )

    def test_login_url(self) -> None:
        self.assertEqual(
            "login",
            classify_linkedin_page("https://www.linkedin.com/login"),
        )

    def test_uas_login_url(self) -> None:
        self.assertEqual(
            "login",
            classify_linkedin_page(
                "https://www.linkedin.com/uas/login?session_redirect=x"
            ),
        )

    def test_checkpoint_url(self) -> None:
        self.assertEqual(
            "checkpoint",
            classify_linkedin_page(
                "https://www.linkedin.com/checkpoint/challenge/xyz"
            ),
        )

    def test_authwall_url(self) -> None:
        self.assertEqual(
            "authwall",
            classify_linkedin_page(
                "https://www.linkedin.com/authwall?trk=qf"
            ),
        )

    def test_unknown_url(self) -> None:
        self.assertEqual(
            "unknown",
            classify_linkedin_page("https://example.com/"),
        )


if __name__ == "__main__":
    unittest.main()
