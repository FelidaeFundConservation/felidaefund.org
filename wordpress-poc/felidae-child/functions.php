<?php
function felidae_child_enqueue_styles() {
    wp_enqueue_style(
        'felidae-google-fonts',
        'https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Literata:ital,opsz,wght@0,7..72,300;0,7..72,400;0,7..72,500;1,7..72,400&display=swap',
        [],
        null
    );
    wp_enqueue_style(
        'felidae-child-style',
        get_stylesheet_uri(),
        [],
        wp_get_theme()->get( 'Version' )
    );
}
add_action( 'wp_enqueue_scripts', 'felidae_child_enqueue_styles' );

function felidae_child_editor_styles() {
    add_editor_style( [
        'https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Literata:ital,opsz,wght@0,7..72,300;0,7..72,400;0,7..72,500;1,7..72,400&display=swap',
        get_stylesheet_uri(),
    ] );
}
add_action( 'after_setup_theme', 'felidae_child_editor_styles' );
