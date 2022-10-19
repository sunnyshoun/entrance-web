var geptLevels = {'w1':'初級', 'w2':'中級', 'w3':'中高'};
var geptTestTypes = {'fill_in_the_blank':'填空題', 'multiple_choice':'選擇題'};
var geptLevelClasses = {'w1':'texti-w1', 'w2':'texti-w2', 'w3':'texti-w3'};

function alertError(argMsg) {
    if(argMsg==0) {
        toastr.error('伺服器沒有回應');
    }
    else if(argMsg==500) {
        toastr.error('內部伺服器錯誤');
    }
    else {
        toastr.error(argMsg);
    }
}

function bool2bin(argVal) {
    return argVal == true ? 1 : 0;
}

function getColor() {
    var R = parseInt(Math.random()*128+50).toString(16).padStart(2, '0');
    var G = parseInt(Math.random()*128+50).toString(16).padStart(2, '0');
    var B = parseInt(Math.random()*128+50).toString(16).padStart(2, '0');
    return '#'+R+G+B;
}

String.prototype.replaceAll = function(argFind, argRep){
    return this.replace(new RegExp(argFind, 'gm'),argRep);
}

Number.prototype.currency = function() {
    var astr = this.toFixed(1).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    return astr.substring(0, astr.indexOf('.'));
};