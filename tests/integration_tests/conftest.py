
def pytest_addoption(parser):
    parser.addoption(
        '--image-name',
        default='cloudify-manager-aio',
        help='Name of the Cloudify Manager AIO docker image',
    )
