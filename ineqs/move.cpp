#include <iostream>
#include <cstdint>

using namespace std;

union Value {
    struct {
        uint16_t go : 1, stop : 1, cont : 1, // decision vars
                 n0 : 1, n1 : 1, n2 : 1, n3 : 1, n4 : 1, n5 : 1, //node vars
                 e1 : 1, e2 : 1, e3 : 1, e4 : 1, // edge vars
                 en0 : 1; // end node stat at end
    } vars;
    uint16_t packed;
};

inline bool check(Value & v) {
    auto & k = v.vars;
    if (k.n0 && k.go) {
        // car is there and go was ordered
        bool edges = k.e1 && k.e2 && k.e3 && k.e4;
        if (!edges)
            return false;
        bool nstat = k.n1 && k.n2 && k.n3 && k.n4 && k.n5;
        if (!nstat)
            return false;
        if (!k.en0)
            return false;
        return k.cont != k.stop;
    }
    return true;
}

inline void print(Value & val) {
    auto & k = val.vars;
    printf("%d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
            k.go, k.stop, k.cont,
            k.n0, k.n1, k.n2, k.n3, k.n4, k.n5,
            k.e1, k.e2, k.e3, k.e4,
            k.en0);
}

int main() {
    Value v;
    for (uint16_t i = 0; i < 16384; ++i) {
        v.packed = i;
        if (check(v))
            print(v);
    }
    return 0;
}
