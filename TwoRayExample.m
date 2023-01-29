o1 = [0 -4 1];
v1 = [-0.1026 -0.6233 1];

o2 = [0 -4 1] * rotz(90);
v2 = [-0.06212 -0.6399 1] * rotz(90);

% Create data matrix
origin = [o1; o2];
vec = [v1/norm(v1); v2/norm(v2)];

% Calculate position
P = calculate_led_pos(origin, vec)

% Plot closest point
plot_lines(origin, vec, P)
axis([-10 10 -10 10 -10 10])