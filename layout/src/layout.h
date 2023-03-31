//
//  layout.h
//  layout++
//
//  Created by Andrei Kashcha on 5/21/15.
//  Copyright (c) 2015 Andrei Kashcha. All rights reserved.
//

#ifndef __layout____layout__
#define __layout____layout__

#include "Random.h"
#include "primitives.h"
#include "quadTree.h"
#include <vector>

using namespace std;

class Layout {
  Random random;
  vector<Body> bodies;
  LayoutSettings settings;
  QuadTree tree;

  void accumulate();
  double integrate();
  void updateDragForce(Body *body);
  void updateSpringForce(Body *spring);

  void initBodies(int *links, long size);

  void setDefaultBodiesPositions();
  void loadPositionsFromArray(int *initialPositions);

public:
  Layout();
  void init(int *links, long linksSize, int *initialPositions, size_t posSize);
  void init(int *links, long size);
  void setBodiesWeight(int *weights);
  void divideBodiesWeight (int divisor);
  bool step();
  size_t getBodiesCount();
  vector<Body> *getBodies() { 
    vector<int> weights(bodies.size(), 1);
    setBodiesWeight(weights.data());
    return &bodies; 
  };
};

#endif /* defined(__layout____layout__) */
