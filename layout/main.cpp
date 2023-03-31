// reading an entire binary file
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <unistd.h>

#include "layout.h"

using namespace std;

void save(const std::string &filename, std::vector<Body> *bodies) {
  std::ofstream outfile(filename, std::ofstream::binary);

  char block[3 * 4];
  int *triplet = (int *)&block;
  for (vector<Body>::iterator body = bodies->begin(); body != bodies->end();
       ++body) {
    triplet[0] = floor(body->pos.x + 0.5);
    triplet[1] = floor(body->pos.y + 0.5);
    triplet[2] = floor(body->pos.z + 0.5);
    //    cout << triplet[0] << "," << triplet[1] << "," << triplet[2] << " <-
    //    node" << endl;
    outfile.write(block, 3 * 4);
  }
  outfile.close();
}

void save_config(const std::string &filename){
  std::ofstream outfile(filename);

  LayoutSettings setting = LayoutSettings();
  outfile << "stableThreshold: "<< setting.stableThreshold<<endl;
  outfile << "gravity: "<<setting.gravity<<endl;
  outfile << "theta: "<<setting.theta<<endl;
  outfile << "dragCoeff: "<<setting.dragCoeff<<endl;
  outfile << "springCoeff: "<<setting.springCoeff<<endl;
  outfile << "springLength: "<<setting.springLength<<endl;
  outfile << "timeStep: "<<setting.timeStep<<endl;
  outfile.close();
}

typedef struct {
  int *content;
  long size;
} FileContent;

FileContent *readFile(const char *fileName) {
  streampos size;
  char *memblock;
  ifstream file(fileName, ios::in | ios::binary | ios::ate);

  if (file.is_open()) {
    size = file.tellg();
    memblock = new char[size];
    file.seekg(0, ios::beg);
    file.read(memblock, size);
    file.close();
    FileContent *result = new FileContent();
    result->size = size / 4;
    result->content = (int *)memblock;
    return result;
  } else {
    return nullptr;
  }
}

int getIterationNumberFromPositionFileName(const char *positionFileName) {
  cmatch match;
  regex pattern(".*?(\\d+)\\.bin$");
  regex_match(positionFileName, match, pattern);
  if (match.size() == 2) {
    try {
      return stoi(match[1]) + 1;
    } catch (...) {
      return 0;
    }
  }
  return 0;
}

int main(int argc, const char *argv[]) {
  if (argc < 3) {
    cout
        << "Usage: " << endl
        << "  " << argv[0] << " links.bin [positions.bin]" << endl
        << "Where" << endl
        << " `links.bin` is a path to the serialized graph. See " << endl
        << "    https://github.com/anvaka/ngraph.tobinary for format "
           "description"
        << endl
        << "  `positions.bin` is optional file with previously saved "
           "positions. "
        << endl
        << "    This file should match `links.bin` graph, otherwise bad things "
        << endl
        << "    will happen" << endl;

    cout << "We expect the second argument to be the output dir where we will dump the positions.bin files" << endl;
    return -1;
  }

  const char *graphFileName = argv[1];
  std::cout<<"this is ok"<<endl;
  string outputDir = argv[2];
  std::cout<<"this is ok"<<endl;
  srand(42);

  char cwd[1024];
  if (getcwd(cwd, 1024) != NULL) {
    cout << cwd << endl;
  } else {
    cout << errno;
  }

  cout << "Loading links from " << graphFileName << "... " << endl;
  FileContent *graphFilePtr = readFile(graphFileName);
  if (graphFilePtr == nullptr) {
    throw "Could not read links file";
  }
  FileContent graphFile = *graphFilePtr;

  Layout graphLayout;
  int startFrom = 0;
  if (argc < 4) {
    graphLayout.init(graphFile.content, graphFile.size);
    cout << "Done. " << endl;
    cout << "Loaded " << graphLayout.getBodiesCount() << " bodies;" << endl;
  } else {
    const char *posFileName = argv[3];
    startFrom = getIterationNumberFromPositionFileName(posFileName);
    cout << "Loading positions from " << posFileName << "... ";
    FileContent *positions = readFile(posFileName);
    if (positions == nullptr)
      throw "Positions file could not be read";

    cout << "Done." << endl;
    graphLayout.init(graphFile.content, graphFile.size, positions->content,
                     positions->size);
    cout << "Loaded " << graphLayout.getBodiesCount() << " bodies;" << endl;
  }
  // TODO: This should be done via arguments, but doing it inline now:
  // If current folder containsfil 'weights.bin' we will try to assign
  // nodes weights from this file
  FileContent *weights = readFile("weights.bin");
  if (weights != nullptr) {
    cout << "Detected weights.bin file in the current folder." << endl;
    cout << "Assuming each node has assigned body weight. Reading weights..."
         << endl;
    cout << "Size: " << weights->size;
    graphLayout.setBodiesWeight(weights->content);
  }

  cout << "Starting layout from " << startFrom << " iteration;" << endl;

  for (int i = startFrom; i < 10000; ++i) {
    cout << "Step " << i << endl;
    bool done = graphLayout.step();
    if (done) {
      cout << "Done!" << endl;
      break;
    }
    if (i % 500 == 0) {
      save(outputDir + "/"+std::to_string(i) + ".bin", graphLayout.getBodies());
    }
  }

  std::cout<<"The ouptut dir is: "<<outputDir<<endl;

  save(outputDir + "/"+"positions.bin", graphLayout.getBodies());

  save_config(outputDir +"/layout_primitives");

  delete[] graphFile.content;
}
