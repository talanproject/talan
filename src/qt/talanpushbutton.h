#ifndef TALANPUSHBUTTON_H
#define TALANPUSHBUTTON_H
#include <QPushButton>
#include <QStyleOptionButton>
#include <QIcon>

class TalanPushButton : public QPushButton
{
public:
    explicit TalanPushButton(QWidget * parent = Q_NULLPTR);
    explicit TalanPushButton(const QString &text, QWidget *parent = Q_NULLPTR);

protected:
    void paintEvent(QPaintEvent *) Q_DECL_OVERRIDE;

private:
    void updateIcon(QStyleOptionButton &pushbutton);

private:
    bool m_iconCached;
    QIcon m_downIcon;
};

#endif // TALANPUSHBUTTON_H
