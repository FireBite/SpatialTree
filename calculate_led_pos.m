function [P, error] = calculate_led_pos(origin, vec)
    % Input sanitization
    if (size(origin,1) ~= size(vec,1))
        error("Mismatched origin (%d) and vector (%d) sizes", size(origin,1), size(vec,1))
    end
    
    norm_m = @(v) sqrt(sum(v.^2,2));
    dist = @(o, v, p) norm_m(cross(v./norm_m(v), (o - p), 2)).^2;
    
    % Minimalize line-to-point distance function
    fun = @(x) sum(dist(origin,vec,x));
    P = fminsearch(fun, [0,0,0]);
    
    % Calculate position uncertainity
    error = std(dist(origin, vec, P));
end

