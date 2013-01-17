Index: geos/source/index/bintree/Node.cpp
===================================================================
--- geos.orig/source/index/bintree/Node.cpp	2011-05-25 12:56:17.000000000 +0200
+++ geos/source/index/bintree/Node.cpp	2011-05-25 12:58:49.000000000 +0200
@@ -15,6 +15,7 @@
  **********************************************************************/
 
 #include <cassert>
+#include <cstddef>
 
 #include <geos/index/bintree/Node.h>
 #include <geos/index/bintree/Key.h>
@@ -24,6 +25,8 @@
 namespace index { // geos.index
 namespace bintree { // geos.index.bintree
 
+using namespace std;
+
 Node*
 Node::createNode(Interval *itemInterval)
 {
Index: geos/source/geomgraph/Node.cpp
===================================================================
--- geos.orig/source/geomgraph/Node.cpp	2011-05-25 12:56:17.000000000 +0200
+++ geos/source/geomgraph/Node.cpp	2011-05-25 13:00:59.000000000 +0200
@@ -30,6 +30,7 @@
 #include <sstream>
 #include <vector>
 #include <algorithm>
+#include <cstddef>
 
 #ifndef GEOS_DEBUG
 #define GEOS_DEBUG 0
@@ -38,12 +39,13 @@
 #define COMPUTE_Z 1
 #endif
 
-using namespace std;
 using namespace geos::geom;
 
 namespace geos {
 namespace geomgraph { // geos.geomgraph
 
+using namespace std;
+
 /*public*/
 Node::Node(const Coordinate& newCoord, EdgeEndStar* newEdges)
 	:
Index: geos/source/index/quadtree/Node.cpp
===================================================================
--- geos.orig/source/index/quadtree/Node.cpp	2011-05-25 12:56:17.000000000 +0200
+++ geos/source/index/quadtree/Node.cpp	2011-05-25 13:02:00.000000000 +0200
@@ -25,6 +25,7 @@
 #include <string>
 #include <sstream>
 #include <cassert>
+#include <cstddef>
 
 #ifndef GEOS_DEBUG
 #define GEOS_DEBUG 0
@@ -41,6 +42,8 @@
 namespace index { // geos.index
 namespace quadtree { // geos.index.quadtree
 
+using namespace std;
+
 /* public static */
 std::auto_ptr<Node>
 Node::createNode(const Envelope& env)
