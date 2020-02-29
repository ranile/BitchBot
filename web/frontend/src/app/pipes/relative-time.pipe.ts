import {Pipe, PipeTransform} from '@angular/core';

const milliSecondsInDay = 1000 * 60 * 60 * 24;
const milliSecondsInHour = 1000 * 60 * 60;
const milliSecondsInMinute = 1000 * 60;

const rtf = new (Intl as any).RelativeTimeFormat('en');

@Pipe({
    name: 'relativeTime'
})
export class RelativeTimePipe implements PipeTransform {

    transform(epochTime: number): string {
        const diffInMilliseconds = (epochTime * 1000) - new Date().getTime();
        const formattedDays = rtf.format(Math.round(diffInMilliseconds / milliSecondsInDay), 'day');

        const formattedHour = formattedDays !== '0 days ago' ? formattedDays :
            rtf.format(Math.round(diffInMilliseconds / milliSecondsInHour), 'hour');

        const formattedMinute = formattedHour !== '0 hours ago' ? formattedHour :
            rtf.format(Math.round(diffInMilliseconds / milliSecondsInMinute), 'minutes');

        return (formattedMinute !== '0 minutes ago') ? formattedMinute : 'Just now';
    }

}
