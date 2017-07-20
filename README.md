DirMap - The Directory Mapper
=============================

Useful for systematically translating paths from one environment to another
in which volumes are mounted differently, or directories otherwise moved.

The smallest example:

~~~
>>> dirmap = DirMap({'/src': '/dst'})
>>> dirmap('/src/something')
'/dst/something'
~~~
