CKEDITOR.editorConfig = function( config ) {
    config.allowedContent: true,
    config.protectedSource: /<ins[\s|\S]+?<\/ins>/g
};
