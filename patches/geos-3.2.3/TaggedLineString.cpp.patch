Index: geos/source/simplify/TaggedLineString.cpp
===================================================================
--- geos.orig/source/simplify/TaggedLineString.cpp	2011-05-25 17:04:12.000000000 +0200
+++ geos/source/simplify/TaggedLineString.cpp	2011-05-25 17:04:31.000000000 +0200
@@ -27,6 +27,7 @@
 
 #include <cassert>
 #include <memory>
+#include <cstddef>
 
 #ifndef GEOS_DEBUG
 #define GEOS_DEBUG 0
@@ -42,6 +43,8 @@
 namespace geos {
 namespace simplify { // geos::simplify
 
+using namespace std;
+
 /*public*/
 TaggedLineString::TaggedLineString(const geom::LineString* nParentLine,
 			size_t nMinimumSize)
