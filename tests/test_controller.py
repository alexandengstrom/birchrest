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

    @patch('birchrest.Controller.__subclasses__', return_value=[])
    def test_no_subcontrollers_discovered(self, mock_subclasses):
        """Test that no subcontrollers are discovered if there are no subclasses."""
        controller = birchrest.Controller()

        # Assert no controllers are attached
        self.assertEqual(controller.controllers, [])
        mock_subclasses.assert_called_once()

    def test_dynamic_subcontroller_discovery(self):
        """Test that subcontrollers are dynamically discovered and initialized."""
        class SubController(birchrest.Controller):
            pass
        
        class SubSubController(SubController):
            pass

        controller = SubController()

        self.assertEqual(len(controller.controllers), 1)


    @patch('birchrest.routes.Route')
    def test_resolve_paths(self, MockRoute):
        """Test that resolve_paths correctly updates route paths and middlewares."""
        mock_route = Mock()
        self.controller.routes = [mock_route]
        
        mock_subcontroller = Mock(spec=birchrest.Controller)
        self.controller.controllers = [mock_subcontroller]

        self.controller.resolve_paths(prefix="/api", middlewares=["middleware1"])

        mock_route.resolve.assert_called_with("/api", ["middleware1"])

        mock_subcontroller.resolve_paths.assert_called_with("/api", ["middleware1"])
        
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
