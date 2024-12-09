import unittest
from unittest.mock import MagicMock, patch
from main import main

class TestMainIntegration(unittest.TestCase):
    def setUp(self):
        """Set up mocked database connection and cursor."""
        self.connection = MagicMock()
        self.cursor = MagicMock()
        self.connection.cursor.return_value = self.cursor
        # Inject mocked objects into main.py
        patcher_connection = patch('main.connection', self.connection)
        patcher_cursor = patch('main.cursor', self.cursor)
        self.addCleanup(patcher_connection.stop)
        self.addCleanup(patcher_cursor.stop)
        patcher_connection.start()
        patcher_cursor.start()

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        # Login sequence
        'b', '1',
        # Quit program
        'q', 'c', 'q', 'q'
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_login_and_quit(self, mock_getpass, mock_input, mock_connect):
        """Test logging in as an existing user and quitting."""
        # Mock database response for login
        self.cursor.fetchone.return_value = (1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC')
        with patch('builtins.print') as mock_print:
            main()
            # Verify `cursor.execute()` is called correctly in login.py
            self.cursor.execute.assert_called()
            # Verify printed output
            mock_print.assert_any_call("Login successful, welcome Test User!")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        # Signup sequence
        'a', 'New User', 'new@example.com', 'New City', 'UTC',
        # Quit program
        'q', 'c', 'q'
    ])
    @patch('getpass.getpass', side_effect=['newpassword', 'newpassword'])
    def test_signup_and_quit(self, mock_getpass, mock_input, mock_connect):
        """Test signing up a new user and quitting."""
        # Mock database response for signup
        self.cursor.fetchone.return_value = None
        with patch('builtins.print') as mock_print:
            main()
            # Verify `cursor.execute()` is called correctly in login.py for signup
            self.cursor.execute.assert_called()
            # Verify printed output
            mock_print.assert_any_call("Thank you for signing up, New User! Your userID is 1.")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        # Login with incorrect password
        'b', '1',
        # Quit program
        'q'
    ])
    @patch('getpass.getpass', return_value='wrongpassword')
    def test_failed_login(self, mock_getpass, mock_input, mock_connect):
        """Test failed login attempt."""
        # Mock database response for login
        self.cursor.fetchone.return_value = None

        with patch('builtins.print') as mock_print:
            main()
            # Verify `cursor.execute()` is called for login attempt
            self.cursor.execute.assert_called()
            # Verify printed output
            mock_print.assert_any_call("Login failed! Please recheck your credentials and try again.")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        'b', '1', 'c',  # Login
        't', 'test', 'b',  # Search for Tweets
        'q', 'q'  # Logout and Quit
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_search_tweets(self, mock_getpass, mock_input, mock_connect):
        """Test the 'Search for Tweets' option."""
        # Mock login
        self.cursor.fetchone.side_effect = [(1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC'), [("User1", 2, "2024-01-02", "First Tweet", 101), ("User2", 3, "2024-01-02", "Second Tweet", 102),
             ("User3", 4, "2024-01-02", "Third Tweet", 103), ("User4", 5, "2024-01-02", "Fourth Tweet", 104),
             ("User5", 6, "2024-01-02", "Fifth Tweet", 105), ("User6", 7, "2024-01-02", "Sixth Tweet", 106)]]

        with patch('builtins.print') as mock_print:
            main()
            # Assert cursor.execute was called during search
            self.cursor.execute.assert_called()
            # Verify printed outputs
            mock_print.assert_any_call("---------Search for Tweets---------")
            mock_print.assert_any_call("Matching tweets:\n")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        'b', '1', # Login
        'u', 'Test', '0',  # Search Users
        'q', 'q'  # Logout and Quit
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_search_users(self, mock_getpass, mock_input, mock_connect):
        """Test the 'Search for Users' option."""
        # Mock login
        self.cursor.fetchone.side_effect = [(1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC'),
            (1,), (1,)]
        self.cursor.fetchall.side_effect = [[], [], [(1, "test_user1", "Test User 1")], [(2, "test_user2", "Test User 2")]]  # Name and city search results

        with patch('builtins.print') as mock_print:
            main()
            # Assert cursor.execute was called during search
            self.cursor.execute.assert_called()
            # Verify printed outputs
            mock_print.assert_any_call("----------Search for Users----------")
            mock_print.assert_any_call("1- (ID:1) test_user1")
            mock_print.assert_any_call("2- (ID:2) test_user2")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        'b', '1', 'c',  # Login
        'c', 'This is a test tweet!',  # Compose a Tweet
        'q', 'q'  # Logout and Quit
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_compose_tweet(self, mock_getpass, mock_input, mock_connect):
        """Test the 'Compose a Tweet' option."""
        # Mock login
        self.cursor.fetchone.side_effect = [
            (1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC'),  # Login
            (1,)  # Tweet ID
        ]

        with patch('builtins.print') as mock_print:
            main()

            # Assert cursor.execute was called during tweet composition
            self.cursor.execute.assert_called()
            # Verify printed outputs
            mock_print.assert_any_call("-------Composing a New Tweet--------")
            mock_print.assert_any_call("Your tweet...")
            mock_print.assert_any_call("    Test User : This is a test tweet!")
            mock_print.assert_any_call("...has been made!")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        'b', '1',  # Login
        'l', '0',  # List Followers
        'q', 'q'  # Logout and Quit
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_list_followers(self, mock_getpass, mock_input, mock_connect):
        """Test the 'List Followers' option."""
        # Mock login
        self.cursor.fetchone.return_value = (1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC')
        self.cursor.fetchall.side_effect = [[], [], [(2, "Follower1", "Follower 1"), (3, "Follower2", "Follower 2")]]

        with patch('builtins.print') as mock_print:
            main()
            # Assert cursor.execute was called during follower listing
            self.cursor.execute.assert_called()
            # Verify printed outputs
            mock_print.assert_any_call("----------List Followers-----------")
            mock_print.assert_any_call("1. Follower1 (User ID: 2)")
            mock_print.assert_any_call("2. Follower2 (User ID: 3)")

    @patch('main.connect', return_value=None)
    @patch('sys.argv', ['main.py', '../test1.db'])
    @patch('builtins.input', side_effect=[
        'b', '1', 'c',  # Login
        'q',  # Logout
        'q'  # Quit
    ])
    @patch('getpass.getpass', return_value='password123')
    def test_logout(self, mock_getpass, mock_input, mock_connect):
        """Test the 'Logout' option."""
        # Mock login
        self.cursor.fetchone.return_value = (1, 'password123', 'Test User', 'test@example.com', 'Test City', 'UTC')

        with patch('builtins.print') as mock_print:
            main()

            # Verify printed outputs
            mock_print.assert_any_call("Logout successful, goodbye Test User!")
