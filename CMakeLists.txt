cmake_minimum_required(VERSION 3.15)
project(PhysicsEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Common source files
set(COMMON_SRC
    src/core/RigidBody.cpp
    src/core/Vec2.cpp
    src/dynamics/Integrator.cpp
    src/collision/CollisionDetector.cpp
)

# Main simulation
add_executable(physics_engine src/main.cpp ${COMMON_SRC})

# Benchmarks
add_executable(benchmark src/benchmark.cpp ${COMMON_SRC})
add_executable(spring_benchmark src/spring_benchmark.cpp ${COMMON_SRC})

# Compiler flags
target_compile_options(physics_engine PRIVATE -Wall -Wextra)
target_compile_options(benchmark PRIVATE -Wall -Wextra)
target_compile_options(spring_benchmark PRIVATE -Wall -Wextra)
