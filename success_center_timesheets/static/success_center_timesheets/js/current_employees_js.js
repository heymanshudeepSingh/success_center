window.onload =function (){
          delete_box = document.querySelectorAll('input[type=checkbox]');

      for(let i=0; i<delete_box.length; i++)
      {
        console.log(delete_box[i].checked);
      }

      submit_btn = document.querySelectorAll('input[type=submit]');
      let del_bool = false;
      submit_btn[0].addEventListener("click",function confirm_delete()
        {
          for(let i=0; i<delete_box.length; i++)
            {
              if (delete_box[i].checked)
                {
                    del_bool = true;

                }
            }
          if (del_bool === true)
          {
            if(window.confirm("Do you want to deleted the checked users?"))
                  {
                    document.getElementById("currentEmployeesForm").submit();
                  }
                  else
                  {
                    delete_box[i].checked = false;
                  }
          }
        }
      )


}
