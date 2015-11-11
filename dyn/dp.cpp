#include <iostream>
#include <list>
#include <unordered_map>
#include <vector>
#include <cstring>
#include <stack>

using namespace std;

enum Spot : uint8_t {
    EMPTY = 0,
    CAR = 1,
    ROBOT = 2,
    CARGO = 4
};

constexpr int DEST = 3;
constexpr int W = 4;
constexpr int H = 4;
constexpr int SIZE = W*H;

struct State {
    Spot state[SIZE];
    inline bool cargoInDest() const {
        return state[DEST] & CARGO;
    }
};

list<State> allStates;

inline void findRobots(Spot * state, int & r1, int & r2) {
    bool first = true;
    for (int i = 0; i < SIZE; ++i) {
        if (state[i] & ROBOT) {
            if (first) {
                first = false;
                r1 = i;
            } else {
                r2 = i;
                return;
            }
        }
    }
}

void addState(Spot * st) {
    State s;
    memcpy(s.state, st, SIZE);
    //TODO: add
}

void generateChildren(State & st) {
    Spot tmp[16];
    memcpy(tmp, st.state, SIZE);
    int r1,r2;
    findRobots(st.state, r1, r2);
}

int main() {
    State st;
    uint8_t initialState[SIZE] = {1,1,2,2,
                                  1,1,4,1,
                                  1,1,1,1,
                                  1,1,1,1};
    memcpy(st.state, initialState, SIZE);
    while (!st.cargoInDest()) {

    }
    return 0;
}
