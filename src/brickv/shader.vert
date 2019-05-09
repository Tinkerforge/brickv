#ifdef GL_ES
// Set default precision to medium
precision mediump int;
precision mediump float;
#endif

varying vec4 frag_pos;
varying vec3 normal;

uniform mat4 model_matrix;
uniform mat4 mvp_matrix;
uniform mat4 normal_matrix;

attribute vec4 a_position;
attribute vec4 a_normal;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;


void main()
{
    gl_Position = mvp_matrix * a_position;

    // If the texture coordinates are both 0.0, this vertex is
    // marked to ignore lighting and always use a constant color.
    // This color is encoded in the vertex normal, so don't apply
    // the normal matrix here.
    if(a_texcoord.x == 0.0 && a_texcoord.y == 0.0)
        normal = a_normal.xyz;
    else
        // GLSL 110 does not support mat3 construction from a mat4
        normal = mat3(normal_matrix[0].xyz, normal_matrix[1].xyz, normal_matrix[2].xyz) * a_normal.xyz;

    frag_pos = model_matrix * a_position;

    v_texcoord = a_texcoord;
}
