Index: geos/source/index/bintree/Root.cpp
===================================================================
--- geos.orig/source/index/bintree/Root.cpp	2011-05-25 13:02:47.000000000 +0200
+++ geos/source/index/bintree/Root.cpp	2011-05-25 13:03:44.000000000 +0200
@@ -20,11 +20,14 @@
 #include <geos/index/quadtree/IntervalSize.h>
 
 #include <cassert>
+#include <cstddef>
 
 namespace geos {
 namespace index { // geos.index
 namespace bintree { // geos.index.bintree
 
+using namespace std;
+
 double Root::origin=0.0;
 
 void
Index: geos/source/index/quadtree/Root.cpp
===================================================================
--- geos.orig/source/index/quadtree/Root.cpp	2011-05-25 13:02:47.000000000 +0200
+++ geos/source/index/quadtree/Root.cpp	2011-05-25 13:03:17.000000000 +0200
@@ -25,6 +25,7 @@
 #include <geos/geom/Envelope.h>
 
 #include <cassert>
+#include <cstddef>
 
 #ifndef GEOS_DEBUG
 #define GEOS_DEBUG 0
@@ -40,6 +41,8 @@
 namespace index { // geos.index
 namespace quadtree { // geos.index.quadtree
 
+using namespace std;
+
 // the singleton root quad is centred at the origin.
 //Coordinate* Root::origin=new Coordinate(0.0, 0.0);
 const Coordinate Root::origin(0.0, 0.0);
