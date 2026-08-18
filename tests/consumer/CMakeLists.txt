cmake_minimum_required(VERSION 3.16)
project(lwbgt_consumer LANGUAGES C)

find_package(lwbgt 0.2 CONFIG REQUIRED)
add_executable(lwbgt_static_consumer main.c)
add_executable(lwbgt_shared_consumer main.c)
target_link_libraries(lwbgt_static_consumer PRIVATE lwbgt::static)
target_link_libraries(lwbgt_shared_consumer PRIVATE lwbgt::shared)
