import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { IInput } from 'src/app/interfaces/common/IInput';

@Component({
  selector: 'app-input-component',
  templateUrl: './input-component.component.html',
  styleUrls: ['./input-component.component.scss']
})
export class InputComponentComponent {

  @Input() input: IInput;
  @Input() form: FormGroup;

  isValid() {
    const control = this.form.controls[this.input.id];
    if (!control) {
      return true;
    }
    return control.valid;

  }

}
