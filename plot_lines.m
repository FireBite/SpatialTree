function plot_lines(origin, vec, P)
%PLOTLINES Draws rays and the calculated point
    line = @(o, v, t) o + (v/norm(v)).*t';
    len = size(origin, 1);

    % Plot the closest point
    plot3(P(1), P(2), P(3), 'or');
    grid on;
    hold on;
        
    % Plot rays
    t = linspace(-10, 10, 100);
    for i = 1:len
        % Draw line
        l = line(origin(i,:), vec(i,:), t);
        plot3(l(:,1),l(:,2),l(:,3))

        % Draw camera origin
        plot3(origin(i,1), origin(i,2), origin(i,3), 'ok');
    end

    % Annotate plot
    title("Raytrace visualization")
    xlabel("x")
    ylabel("y")
    zlabel("z")

    hold off
end
