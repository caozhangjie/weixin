game.module(
    'game.assets'
)
.body(function() {

game.addAsset('flyingdog/sprites.json');
game.addAsset('flyingdog/font.fnt');

game.addAudio('flyingdog/audio/explosion.m4a', 'explosion');
game.addAudio('flyingdog/audio/jump.m4a', 'jump');
game.addAudio('flyingdog/audio/score.m4a', 'score');
game.addAudio('flyingdog/audio/highscore.m4a', 'highscore');
game.addAudio('flyingdog/audio/music.m4a', 'music');

});
