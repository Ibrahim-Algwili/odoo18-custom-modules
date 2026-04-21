import random

from odoo import _, api, fields, models

list_of_messages = [
    "صلي على أشرف الخلق و المرسلين",
    "سبحان الله وبحمده، سبحان الله العظيم",
    "لا حول ولا قوة إلا بالله العلي العظيم",
    "أستغفر الله الذي لا إله إلا هو الحي القيوم وأتوب إليه",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
    "اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت",
    "سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر",
    "اللهم صلِّ وسلم وبارك على نبينا محمد وعلى آله وصحبه أجمعين",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله ولا تكلني إلى نفسي طرفة عين",
    "رضيت بالله رباً وبالإسلام ديناً وبمحمد ﷺ نبياً",
]


class Notifications(models.Model):
    _name = "notifications"

    def _getting_active_users(self):
        return self.env["res.users"].search([("active", "=", True)])

    def _getting_random_message(self):
        return random.choice(list_of_messages)

    def _generate_notification_message(self, users):
        for user in users:
            self.env["bus.bus"]._sendone(
                user.partner_id,
                "simple_notification",
                {
                    "type": "success",
                    "title": "تذكير",
                    "message": self._getting_random_message(),
                    "sticky": False,
                },
            )

    @api.model
    def _cron_send_notification(self):
        users = self._getting_active_users()
        self._generate_notification_message(users)
