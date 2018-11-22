
python_library(
    name = "build_util",
    srcs = [
        "build_util.py", 
        "pip_show_parser.py",
        "pipenv_graph_parser.py",
    ],
    deps = [
        "//third_party/python:astor",
        "//third_party/python:yapf",
    ],
    visibility = ["//tools"],
)

python_library(
    name = "to_build",
    srcs = ["to_build.py"],
    deps = [
        "//third_party/python:click",
        "//third_party/python:jinja2",
        ":build_util",
    ],
    visibility = ["//tools"],
)

python_library(
    name = "to_req",
    srcs = ["to_req.py"],
    deps = [
        "//third_party/python:click",
    ],
    visibility = ["//tools"],
)
