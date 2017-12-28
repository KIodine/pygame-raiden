from pygame.math import Vector2

a = Vector2( 1,6 )
b = Vector2( 4,3 )

center = Vector2(1,3)

a = a-center
b = b-center

print(a,a.as_polar())
print(b,b.as_polar())


