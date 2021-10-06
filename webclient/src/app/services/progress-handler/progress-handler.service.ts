import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ProgressHandlerService {
  public onActionCompleted: Subject<boolean> = new Subject<boolean>();
  constructor() {}
}
