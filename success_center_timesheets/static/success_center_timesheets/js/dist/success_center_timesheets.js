(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";

window.onload = function () {
  delete_box = document.querySelectorAll('input[type=checkbox]');
  for (var _i = 0; _i < delete_box.length; _i++) {
    console.log(delete_box[_i].checked);
  }
  submit_btn = document.querySelectorAll('input[type=submit]');
  var del_bool = false;
  submit_btn[0].addEventListener("click", function confirm_delete() {
    for (var _i2 = 0; _i2 < delete_box.length; _i2++) {
      if (delete_box[_i2].checked) {
        del_bool = true;
      }
    }
    if (del_bool === true) {
      if (window.confirm("Do you want to deleted the checked users?")) {
        document.getElementById("currentEmployeesForm").submit();
      } else {
        delete_box[i].checked = false;
      }
    }
  });
};

},{}],2:[function(require,module,exports){
"use strict";

var signaturePad;
var image_arr;
var image_arr_2;
var blank;
window.onload = function () {
  CalculateTotal();
  //initially disable submit button
  $('input[id="id_submit"]').prop('disabled', true);
  var mycanvas = document.getElementById("signature"); //get your canvas
  if (mycanvas != null) {
    signature($('#signature').get(0), $('#signature-input').get(0), $('#clear-signature').get(0));
    blank = mycanvas.toDataURL(); //get your canvas
    var image = mycanvas.toDataURL(); //Convert
    image_arr = image.split(',');
    image_arr_2 = image_arr;
    mycanvas.addEventListener('mouseup', function (e) {
      CalculateTotal();
    });
  }
};
function change() {
  document.getElementById("signature-input").value = image_arr[1];
}
// Get Signature
function signature(pad, submit, clear) {
  var signaturePad = new SignaturePad($('#signature').get(0), {
    backgroundColor: '#ffffff',
    penColor: '#000000'
  });
  $('#id_submit').get(0).addEventListener('click', function (event) {
    var dataUrl = signaturePad.toDataURL('image/jpeg');
    $('#signature-input').attr('value', dataUrl);
  });
  $('#clear-signature').get(0).addEventListener('click', function (event) {
    event.preventDefault();
    signaturePad.clear();
    isCanvasBlank();
  });
}

// returns true if every pixel's uint32 representation is 0 (or "blank")
function isCanvasBlank() {
  var canvas = document.getElementById("signature");
  var bool = false;
  if (canvas === null) {
    bool = false;
  } else {
    if (canvas.toDataURL() === blank) {
      bool = true;
    }
  }
  if (bool === true) {
    if (document.getElementById("id_submit") != null) {
      $('input[id="id_submit"]').prop('disabled', true);
      document.getElementById("id_submit").style.opacity = "0.5";
    }
  }
}
function CalculateTotal() {
  var morning_begin_id;
  var evening_begin_id;
  var evening_end_id;
  var afternoon_end_id;
  var afternoon_begin_id;
  var morning_end_id;
  var morning_total;
  var afternoon_total;
  var evening_total;
  var morning_valid = true;
  var afternoon_valid = true;
  var evening_valid = true;
  var all_valid = [];
  var week_one_total = 0;
  var grand_total = 0;

  // loop through all 14 days
  for (var index = 0; index <= 13; index++) {
    // getting individual day id, ex id_morning_begin_1 , 2....
    morning_begin_id = 'id_morning_begin_L';
    morning_begin_id = morning_begin_id.replace("L", index.toString());
    var morning_begin = document.getElementById(morning_begin_id);
    var morning_begin_value = morning_begin.options[morning_begin.selectedIndex].value;
    morning_end_id = 'id_morning_end_L';
    morning_end_id = morning_end_id.replace("L", index.toString());
    var morning_end = document.getElementById(morning_end_id);
    var morning_end_value = morning_end.options[morning_end.selectedIndex].value;
    morning_total = (morning_end_value - morning_begin_value) / 2;

    //Validate Morning Input
    if (morning_end_value > 0 || morning_begin_value > 0) {
      if (morning_begin_value !== '0' && morning_end_value !== '0') {
        morning_valid = morning_total > 0;
      } else {
        morning_valid = false;
      }
    }
    afternoon_begin_id = 'id_afternoon_begin_L';
    afternoon_begin_id = afternoon_begin_id.replace("L", index.toString());
    var afternoon_begin = document.getElementById(afternoon_begin_id);
    var afternoon_begin_value = afternoon_begin.options[afternoon_begin.selectedIndex].value;
    afternoon_end_id = 'id_afternoon_end_L';
    afternoon_end_id = afternoon_end_id.replace("L", index.toString());
    var afternoon_end = document.getElementById(afternoon_end_id);
    var afternoon_end_value = afternoon_end.options[afternoon_end.selectedIndex].value;
    afternoon_total = (afternoon_end_value - afternoon_begin_value) / 2;

    //Validate Afternoon Input
    if (afternoon_end_value > 0 || afternoon_begin_value > 0) {
      if (afternoon_begin_value !== '0' && afternoon_end_value !== '0') {
        afternoon_valid = afternoon_end_value > afternoon_begin_value && afternoon_total > 0;
      } else {
        afternoon_valid = false;
      }
    }
    evening_begin_id = 'id_evening_begin_L';
    evening_begin_id = evening_begin_id.replace("L", index.toString());
    var evening_begin = document.getElementById(evening_begin_id);
    var evening_begin_value = evening_begin.options[evening_begin.selectedIndex].value;
    evening_end_id = 'id_evening_end_L';
    evening_end_id = evening_end_id.replace("L", index.toString());
    var evening_end = document.getElementById(evening_end_id);
    var evening_end_value = evening_end.options[evening_end.selectedIndex].value;
    evening_total = (evening_end_value - evening_begin_value) / 2;

    //Validate Evening Input
    if (evening_end_value > 0 || evening_begin_value > 0) {
      if (evening_begin_value !== '0' && evening_end_value !== '0') {
        evening_valid = evening_end_value > evening_begin_value && evening_total > 0;
      } else {
        evening_valid = false;
      }
    }
    var shift_total = morning_total + afternoon_total + evening_total;
    if (shift_total < 0) {
      shift_total = 0;
    }
    grand_total += shift_total;
    document.getElementById(index.toString()).innerHTML = shift_total.toString();

    // if whole day data is valid, append it to list
    all_valid[index] = morning_valid && afternoon_valid && evening_valid;

    //check if each day is valid
    if (all_valid.every(function (v) {
      return v === true;
    })) {
      if (document.getElementById("id_submit") != null) {
        $('input[id="id_submit"]').prop('disabled', false);
        document.getElementById("id_submit").style.opacity = "1";
      }
      isCanvasBlank(blank);
    } else {
      $('input[id="id_submit"]').prop('disabled', true);
      document.getElementById("id_submit").style.opacity = "0.5";
    }
    if (index === 6) {
      week_one_total = grand_total;
      document.getElementById('week_one_total').innerHTML = grand_total.toString();
    }
    if (index === 13) {
      document.getElementById('week_two_total').innerHTML = (grand_total - week_one_total).toString();
    }
  }
  document.getElementById('grand_total').innerHTML = grand_total.toString();

  // Make submit button disabled if the timesheet is empty
  if (grand_total <= 0) {
    $('input[id="id_submit"]').prop('disabled', true);
    document.getElementById("id_submit").style.opacity = "0.5";
  }
}
function handleSubmit() {
  var error = document.getElementById("error");
  if (document.getElementById("signature-input").value === image_arr_2[1]) {
    console.log("EQUAL");
  }
  if (confirm('Do you want to submit this form?')) {
    //             Tried to compare initial canvas vs changed canvas.
    if (document.getElementById("signature-input").value === image_arr_2[1]) {
      // Changing content and color of content
      error.textContent = "Please enter a valid number";
      error.style.color = "red";
      return false;
    } else {
      error.textContent = "";
      return true;
    }
  } else {
    return false;
  }
}

},{}]},{},[1,2]);
