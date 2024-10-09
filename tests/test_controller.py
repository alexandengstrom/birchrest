# type: ignore

import unittest
from unittest.mock import Mock, patch
import birchrest


class TestController(unittest.TestCase):

    def setUp(self):
        """Set up a Controller instance for testing."""
        self.controller = birchrest.Controller()

    def test_initialization(self):
        """Test that Controller initializes with correct default values."""
        controller = birchrest.Controller()

        self.assertEqual(controller._base_path, "")
        self.assertEqual(controller._middlewares, [])
        self.assertEqual(controller._is_protected, "")
        self.assertEqual(controller.routes, [])
        self.assertEqual(controller.controllers, [])

    def test_attach_controllers(self):
        """Test that attach adds sub-controllers to the controllers list."""
        mock_controller = Mock(spec=birchrest.Controller)

        self.controller.attach(mock_controller)

        self.assertEqual(len(self.controller.controllers), 1)
        self.assertIs(self.controller.controllers[0], mock_controller())


    @patch('birchrest.routes.Route')
    def test_resolve_paths(self, MockRoute):
        """Test that resolve_paths correctly updates route paths and middlewares."""
        mock_route = Mock()
        self.controller.routes = [mock_route]

        self.controller.resolve_paths(prefix="/api", middlewares=["middleware1"])

        mock_route.resolve.assert_called_with("/api", ["middleware1"])
        
    @patch('birchrest.routes.Route')
    def test_resolve_path_without_slash(self, MockRoute):
        """Test that resolve_paths correctly updates route paths and middlewares."""
        mock_route = Mock()
        self.controller.routes = [mock_route]

        self.controller.resolve_paths(prefix="api", middlewares=["middleware1"])

        mock_route.resolve.assert_called_with("/api", ["middleware1"])


    @patch('birchrest.routes.Route')
    def test_resolve_paths_with_protection(self, MockRoute):
        """Test that resolve_paths makes routes protected if necessary."""
        self.controller._is_protected = True

        mock_route = Mock()
        self.controller.routes = [mock_route]

        self.controller.resolve_paths(prefix="/api", middlewares=["middleware1"])

        mock_route.make_protected.assert_called_once()


    def test_collect_routes(self):
        """Test that collect_routes yields all routes from the controller and sub-controllers."""
        mock_route1 = Mock(spec=birchrest.routes.Route)
        mock_route2 = Mock(spec=birchrest.routes.Route)

        self.controller.routes = [mock_route1]
        
        sub_controller = Mock(spec=birchrest.Controller)
        sub_controller.collect_routes.return_value = iter([mock_route2])
        self.controller.controllers = [sub_controller]

        collected_routes = list(self.controller.collect_routes())

        self.assertIn(mock_route1, collected_routes)
        self.assertIn(mock_route2, collected_routes)
