cmake_minimum_required(VERSION 3.16)
project(Lichen)
set(CMAKE_CXX_STANDARD 14)

set(Boost_USE_STATIC_LIBS ON)
find_package(Boost REQUIRED COMPONENTS
    system
    filesystem
)

add_executable(Lichen
    compare_hashes.cpp
    submission.cpp
)

target_link_libraries(Lichen
    Boost::system
    Boost::filesystem
)

target_compile_options(Lichen PRIVATE
    -Wall
    -Wextra
    -Werror
    -g
    -O3
    -funroll-loops
)
target_link_options(Lichen PRIVATE
    -flto
)

include_directories(/usr/local/submitty/Lichen/vendor)

set_target_properties(Lichen PROPERTIES OUTPUT_NAME compare_hashes.out)