#ifdef GL_ES
// Set default precision to medium
precision mediump int;
precision mediump float;
#endif

varying vec4 frag_pos;
varying vec3 normal;

uniform vec3 light_pos;
uniform vec3 light_color;
uniform sampler2D texture;

varying vec2 v_texcoord;

void main()
{
    // If the texture coordinates are both 0.0, this vertex is
    // marked to ignore lighting and always use a constant color.
    // This color is encoded in the vertex normal.
    if(v_texcoord.x == 0.0 && v_texcoord.y == 0.0) {
        gl_FragColor = vec4(normal, 1.0);
        return;
    }

    float ambient_strength = 0.4;
    vec3 ambient = ambient_strength * light_color;

    float diff = max(dot(normalize(normal), normalize(light_pos - frag_pos.xyz)), 0.0);
    vec3 diffuse = diff * light_color;

    gl_FragColor = vec4((ambient + diffuse) * texture2D(texture, v_texcoord).xyz, 1.0);
}
