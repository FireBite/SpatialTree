load capture.mat

points = [];

for i = 1:size(rays,2)
    ray = rays{1, i};

    % Calculate position
    P = calculate_led_pos(ray.origin, ray.vec)
    points = [points; P];

    % Plot raytracing result
    plot_lines(ray.origin, ray.vec, P);
    hold on;
end

% Save point cloud
points
save("points.mat", "points")