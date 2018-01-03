from pygame.math import Vector2

A = Vector2(1, 6)
B = Vector2(4, 3)

center = Vector2(1, 3)

A = A-center
B = B-center

print(A, A.as_polar()[1])
print(B, B.as_polar())
