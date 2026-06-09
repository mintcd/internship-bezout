#include <chrono>
#include <iostream>

const int n = 1e5;
int a[n], s = 0;

// #pragma GCC target("avx2")
int main() {
    for (int i = 0; i < n; ++i) a[i] = 1;

    auto start = std::chrono::high_resolution_clock::now();
    for (int t = 0; t < 100000; t++)
        for (int i = 0; i < n; i++)
            s += a[i];
    auto end = std::chrono::high_resolution_clock::now();

    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "Elapsed: " << ms << " ms\n";

    return 0;
}