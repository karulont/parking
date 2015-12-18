#include <iostream>
#include <cstdint>

using namespace std;

union Value {
    struct {
        uint16_t ne : 1, ne1 : 1, nf : 1, // node vars
                 sn : 1, cn : 1, ss : 1, cs : 1, se : 1, ce : 1, //dec vars
                 sw : 1, cw : 1;
    } vars;
    uint16_t packed;
};

inline void print(Value & val) {
    auto & k = val.vars;
    printf("%d %d %d %d %d %d %d %d %d %d %d\n",
            k.ne, k.ne1, k.nf,
            k.sn, k.cn, k.ss, k.cs, k.se, k.ce, k.sw, k.cw);
}

inline bool check(Value & v) {
    auto & k = v.vars;
    // node empty and empty at t+1
    if (k.ne && k.ne1) {
        // everything else must be zero
        return !(v.packed & ~3);
    }
    if (k.ne && !k.ne1) {
        //something moved here
        if (!k.nf)
            return false;
        bool one = k.sn || k.cn || k.ss || k.cs || k.se || k.ce || k.sw || k.cw;
        int count = __builtin_popcount (v.packed >> 3);
        return one;
    }
    return true;
}

int main() {
    Value v;
    for (uint16_t i = 0; i < 4096; ++i) {
        v.packed = i;
        if (check(v))
            print(v);
    }
    return 0;
}
