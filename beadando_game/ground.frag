#version 330 core
in vec2 out_texture;
out vec4 FragColor;

uniform sampler2D textureSampler;

void main()
{    
    FragColor = texture(textureSampler, out_texture);
}