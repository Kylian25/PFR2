cmake_minimum_required(VERSION 3.10)
project(TestRaspberry)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)

add_executable(images src/images_colors.cpp)
target_link_libraries(images PRIVATE ${OpenCV_LIBS})