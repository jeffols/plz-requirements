Incomplete README.md

code to process "pip show" or "pipenv graph --json" to find missing items from BUILD

pip_show_parser was the first implementation and is more exhaustive when finding transitive dependencies.


TODO:
* "pipenv graph --json" does not list all dependencies at the top level.
* tool does not identify if the "outs" do not match the package name.


~~~
$ ./plz-out/bin/tools/tools.pex to-req third_party/python/BUILD
astor==0.7.1
click==7.0
jinja2==2.10
markupsafe==1.0
yapf==0.24.0
~~~

