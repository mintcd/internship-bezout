#include <iostream>
#include <cstring>
using namespace std;

static bool cpu_supports(const char* name);

int main() {
    cout << cpu_supports("sse") << endl;
    cout << cpu_supports("sse2") << endl;
    cout << cpu_supports("avx") << endl;
    cout << cpu_supports("avx2") << endl;
    cout << cpu_supports("avx512f") << endl;

    return 0;
}

#if defined(_MSC_VER)
#include <intrin.h>
#include <immintrin.h>
#endif

static bool cpu_supports(const char* name) {
#if defined(__GNUC__) || defined(__clang__)
    if (strcmp(name, "sse") == 0) return __builtin_cpu_supports("sse");
    if (strcmp(name, "sse2") == 0) return __builtin_cpu_supports("sse2");
    if (strcmp(name, "avx") == 0) return __builtin_cpu_supports("avx");
    if (strcmp(name, "avx2") == 0) return __builtin_cpu_supports("avx2");
    if (strcmp(name, "avx512f") == 0) return __builtin_cpu_supports("avx512f");
#endif

#if defined(_MSC_VER) && (defined(_M_X64) || defined(_M_IX86))
    int info[4] = {0,0,0,0};
    __cpuid(info, 1);
    int ecx = info[2];
    int edx = info[3];

    if (strcmp(name, "sse") == 0) return (edx & (1 << 25)) != 0;
    if (strcmp(name, "sse2") == 0) return (edx & (1 << 26)) != 0;
    if (strcmp(name, "avx") == 0) {
        bool avxBit = (ecx & (1 << 28)) != 0;
        unsigned long long xcr0 = _xgetbv(0);
        bool osSupports = ((xcr0 & 0x6) == 0x6);
        return avxBit && osSupports;
    }
    if (strcmp(name, "avx2") == 0) {
        int info7[4];
        __cpuidex(info7, 7, 0);
        bool avx2 = (info7[1] & (1 << 5)) != 0;
        unsigned long long xcr0 = _xgetbv(0);
        bool osSupports = ((xcr0 & 0x6) == 0x6);
        return avx2 && osSupports;
    }
    if (strcmp(name, "avx512f") == 0) {
        int info7[4];
        __cpuidex(info7, 7, 0);
        bool avx512f = (info7[1] & (1 << 16)) != 0;
        unsigned long long xcr0 = _xgetbv(0);
        bool osSupports = ((xcr0 & 0xE0) == 0xE0);
        return avx512f && osSupports;
    }
    return false;
#else
    (void)name;
    return false;
#endif
}