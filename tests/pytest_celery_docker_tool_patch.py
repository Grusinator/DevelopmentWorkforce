# import pytest_docker_tools.builder
# import re
#
# def patched_build_fixture_function(callable, scope, wrapper_class, kwargs):
#     original_exec = pytest_docker_tools.builder.exec
#
#     def patched_exec(template, globals):
#         # Replace Windows-style paths with raw string literals
#         template = re.sub(r'((?<=: )|(?<=: \'))([A-Za-z]:\\[^\'"\n]+)', lambda m: 'r' + m.group(2).replace('\\', '\\\\'), template)
#         return original_exec(template, globals)
#
#     pytest_docker_tools.builder.exec = patched_exec
#     try:
#         return pytest_docker_tools.builder.build_fixture_function(callable, scope, wrapper_class, kwargs)
#     finally:
#         pytest_docker_tools.builder.exec = original_exec
#
# # Apply the patch
# pytest_docker_tools.builder.build_fixture_function = patched_build_fixture_function
#
#
#
# import pytest_docker_tools.builder
# import re
#
# def patched_exec(template, globals):
#     # Replace Windows-style paths with forward slashes
#     template = re.sub(r'((?<=: )|(?<=: \'))([A-Za-z]:\\[^\'"\n]+)', lambda m: m.group(1) + m.group(2).replace('\\', '/'), template)
#     return original_exec(template, globals)
#
# original_exec = pytest_docker_tools.builder.exec
# pytest_docker_tools.builder.exec = patched_exec
#
#
# import pytest_docker_tools.builder
# from pytest_docker_tools.factories import build as original_build
# import pytest
#
# def patched_build_fixture_function(callable, scope, wrapper_class, kwargs):
#     @pytest.fixture(scope=scope)
#     def fixture():
#         return callable(**kwargs)
#     return fixture
#
# def patched_build(*args, **kwargs):
#     # Remove problematic arguments
#     kwargs.pop('path', None)
#     kwargs.pop('tag', None)
#     kwargs.pop('buildargs', None)
#
#     # Return a dummy object that can be used as a placeholder
#     class DummyDockerImage:
#         def __init__(self):
#             self.id = "dummy_image_id"
#
#     return DummyDockerImage()
#
# # Apply the patches
# pytest_docker_tools.builder.build_fixture_function = patched_build_fixture_function
# pytest_docker_tools.factories.build = patched_build