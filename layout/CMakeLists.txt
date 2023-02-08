cmake_minimum_required(VERSION 3.4...3.18)

project(ngraph LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(OpenMP REQUIRED)
add_executable(layout main.cpp ./src/layout.cpp ./src/quadTree.cpp)
target_link_libraries(layout PUBLIC OpenMP::OpenMP_CXX)
target_include_directories(layout PRIVATE src)
