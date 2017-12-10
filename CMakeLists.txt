cmake_minimum_required (VERSION 2.6)
project (meccanoid)

# Export MODULE_PATH
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")


include(GetGitRevisionDescription)
git_describe(VERSION)
message(STATUS "VERSION = ${VERSION}")

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/version.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/generated/version.h)
set(version_file "${CMAKE_CURRENT_BINARY_DIR}/version.h")
include_directories(${CMAKE_BINARY_DIR}/generated)
add_definitions('-DVERSION="${VERSION}"')

set(SOURCE_FILES meccanoid.cpp)

#Add the version_file to the project build.
add_executable(${PROJECT_NAME} ${SOURCE_FILES})


