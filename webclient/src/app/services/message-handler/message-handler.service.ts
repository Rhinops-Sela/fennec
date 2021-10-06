import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class MessageHandlerService {
  public onErrorOccured: Subject<string> = new Subject<string>();
  public onUserMessage: Subject<string> = new Subject<string>();
  constructor(private snackBar: MatSnackBar) {
    this.onErrorOccured.subscribe((errorMessage: string) => {
      this.openSnackBar(errorMessage, 'error-scnackbar', 5000);
    });
    this.onUserMessage.subscribe((message: string) => {
      this.openSnackBar(message, 'info-scnackbar', 2000);
    });
  }

  private openSnackBar(message: string, snackbarClass: string, duration: number) {
    this.snackBar.open(message, 'dissmis', {
      duration: duration,
      panelClass: [snackbarClass],
    });
  }

}
