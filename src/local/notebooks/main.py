def compute_tns(N):
    tns = [0] * (N + 1)
    if N >= 1: tns[1] = 1
    if N >= 2: tns[2] = 1
    
    for n in range(3, N + 1):
        tns[n] = ((2*n - 1)*tns[n - 1] + 7*(n - 2)*tns[n - 2]) // (n + 1)
        
    return tns


N = 10
tns_values = compute_tns(N)
print(tns_values)